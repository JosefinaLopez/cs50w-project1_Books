var contador ;
var stars;
function  calificar(item)
{
  contador = item.id[0]; // captura el primer caracter
  let nombre = item.id.substring(1) //captura todo menos el primer caracter
  
  for (let index = 0; index < 5; index++) 
  {
      if(index<contador)
      {
        document.getElementById((index+1)+nombre).style.color="orange";
        }
      else{
        document.getElementById((index+1)+nombre).style.color="black";
      }
  }
    SendStars(contador)
}
async function SendStars(contador){
  const getInput = document.querySelector('[name="stars"]')

  if(getInput){
    getInput.value = contador
    return
  }

  const input = document.createElement('input')
  input.setAttribute('type', 'hidden')
  input.setAttribute('name', 'stars')
  input.setAttribute('value', contador)
  document.querySelector('form').appendChild(input)


}